package com.example.gestionstationskii.mockito;

import com.example.gestionstationskii.entities.Skier;
import com.example.gestionstationskii.entities.Subscription;
import com.example.gestionstationskii.entities.TypeSubscription;
import com.example.gestionstationskii.repositories.ISkierRepository;
import com.example.gestionstationskii.repositories.ISubscriptionRepository;
import com.example.gestionstationskii.services.SubscriptionServicesImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class SubscriptionServicesImplTest {

    @Mock
    private ISubscriptionRepository subscriptionRepository;

    @Mock
    private ISkierRepository skierRepository;

    @InjectMocks
    private SubscriptionServicesImpl subscriptionServices;

    private Subscription monthlySub;
    private Subscription annualSub;

    @BeforeEach
    void setUp() {
        monthlySub = new Subscription();
        monthlySub.setNumSub(1L);
        monthlySub.setStartDate(LocalDate.now());
        monthlySub.setEndDate(LocalDate.now().plusMonths(1)); // important
        monthlySub.setPrice(100f);
        monthlySub.setTypeSub(TypeSubscription.MONTHLY);

        annualSub = new Subscription();
        annualSub.setNumSub(2L);
        annualSub.setStartDate(LocalDate.now());
        annualSub.setEndDate(LocalDate.now().plusYears(1)); // important
        annualSub.setPrice(1000f);
        annualSub.setTypeSub(TypeSubscription.ANNUAL);
    }


    @Test
    void testAddSubscription_Monthly() {
        when(subscriptionRepository.save(any(Subscription.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Subscription saved = subscriptionServices.addSubscription(monthlySub);

        assertEquals(monthlySub.getStartDate().plusMonths(1), saved.getEndDate());
        verify(subscriptionRepository, times(1)).save(any(Subscription.class));
    }

    @Test
    void testAddSubscription_Annual() {
        when(subscriptionRepository.save(any(Subscription.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Subscription saved = subscriptionServices.addSubscription(annualSub);

        assertEquals(annualSub.getStartDate().plusYears(1), saved.getEndDate());
        verify(subscriptionRepository, times(1)).save(any(Subscription.class));
    }

    @Test
    void testRetrieveSubscriptionById() {
        when(subscriptionRepository.findById(1L)).thenReturn(Optional.of(monthlySub));

        Subscription found = subscriptionServices.retrieveSubscriptionById(1L);

        assertNotNull(found);
        assertEquals(TypeSubscription.MONTHLY, found.getTypeSub());
    }

    @Test
    void testGetSubscriptionByType() {
        Set<Subscription> subs = new HashSet<>(Arrays.asList(monthlySub));
        when(subscriptionRepository.findByTypeSubOrderByStartDateAsc(TypeSubscription.MONTHLY)).thenReturn(subs);

        Set<Subscription> result = subscriptionServices.getSubscriptionByType(TypeSubscription.MONTHLY);

        assertEquals(1, result.size());
        verify(subscriptionRepository).findByTypeSubOrderByStartDateAsc(TypeSubscription.MONTHLY);
    }

    @Test
    void testRetrieveSubscriptionsByDates() {
        List<Subscription> list = Arrays.asList(monthlySub, annualSub);
        when(subscriptionRepository.getSubscriptionsByStartDateBetween(any(), any())).thenReturn(list);

        List<Subscription> result = subscriptionServices.retrieveSubscriptionsByDates(
                LocalDate.now().minusDays(1),
                LocalDate.now().plusDays(1)
        );

        assertEquals(2, result.size());
        verify(subscriptionRepository).getSubscriptionsByStartDateBetween(any(), any());
    }

    @Test
    void testRetrieveSubscriptionsScheduled() {
        Skier skier = new Skier();
        skier.setFirstName("John");
        skier.setLastName("Doe");
        skier.setSubscription(monthlySub); // <-- indispensable
        when(skierRepository.findBySubscription(monthlySub)).thenReturn(skier);


        // Make subscriptionRepository return a non-empty list
        when(subscriptionRepository.findDistinctOrderByEndDateAsc())
                .thenReturn(Arrays.asList(monthlySub));



        // This should now work without NPE
        subscriptionServices.retrieveSubscriptions();

        // Verify interactions
        verify(subscriptionRepository, times(1)).findDistinctOrderByEndDateAsc();
        verify(skierRepository, times(1)).findBySubscription(monthlySub);
    }


    @Test
    void testShowMonthlyRecurringRevenue() {
        when(subscriptionRepository.recurringRevenueByTypeSubEquals(TypeSubscription.MONTHLY)).thenReturn(300f);
        when(subscriptionRepository.recurringRevenueByTypeSubEquals(TypeSubscription.SEMESTRIEL)).thenReturn(600f);
        when(subscriptionRepository.recurringRevenueByTypeSubEquals(TypeSubscription.ANNUAL)).thenReturn(1200f);

        subscriptionServices.showMonthlyRecurringRevenue();

        verify(subscriptionRepository, times(3)).recurringRevenueByTypeSubEquals(any());
    }
}
